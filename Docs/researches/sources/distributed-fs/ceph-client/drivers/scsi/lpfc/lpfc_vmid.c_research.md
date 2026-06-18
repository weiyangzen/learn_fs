# sources/distributed-fs/ceph-client/drivers/scsi/lpfc/lpfc_vmid.c

## Purpose
`lpfc_vmid.c` manages LPFC VMID lookup, allocation, registration, tagging, accounting, and reinitialization. VMID lets the driver tag I/O with an application ID or priority/CS_CTL value derived from a host VM UUID, then register that mapping with fabric/firmware through VMID commands.

## Important APIs, Types, And Functions
The exported helpers are `lpfc_get_vmid_from_hashtable()`, `lpfc_vmid_hash_fn()`, `lpfc_vmid_get_appid()`, and `lpfc_reinit_vmid()`. `lpfc_get_vmid_from_hashtable()` searches a vport hash bucket for a matching 16-byte `host_vmid`. `lpfc_vmid_hash_fn()` lowercases ASCII letters and computes a bounded hash with `LPFC_VMID_HASH_SHIFT` and `LPFC_VMID_HASH_MASK`. `lpfc_vmid_get_appid()` is the main fast-path call used when an I/O has a UUID; it returns a VMID tag in `union lpfc_vmid_io_tag` or an error indicating retry/busy/resource failure. `lpfc_reinit_vmid()` resets all VMID slots and hash links after events such as FLOGI completion.

Internal helpers include `lpfc_put_vmid_in_hashtable()`, `lpfc_vmid_update_entry()`, and `lpfc_vmid_assign_cs_ctl()`. Update logic fills either `tag->cs_ctl_vmid` for priority-tag mode or `tag->app_id` for application-header mode, increments per-VM read/write counters, and updates a per-CPU last-I/O timestamp.

## Control Flow
On I/O, `lpfc_vmid_get_appid()` first blocks priority-tag I/O if QFPA is required but not complete, setting `WORKER_CHECK_VMID_ISSUE_QFPA` and returning `-EAGAIN`. It hashes the UUID, takes `vmid_lock` for read, and searches the hash table. A registered hit immediately updates the tag and counters. A hit already registering or deregistering returns `-EBUSY` so the I/O is sent without a VMID tag.

On miss, the function upgrades to the write lock, rechecks for races, locates a free slot if `cur_vmid_cnt < max_vmid`, initializes the slot, inserts it into the hash table, optionally assigns a CS_CTL value, allocates per-CPU timestamp storage, and drops the lock before issuing fabric/firmware registration. Priority-tag mode calls `lpfc_vmid_uvem()`, while app-header mode calls `lpfc_vmid_cmd(..., SLI_CTAS_RAPP_IDENT, ...)`. Successful command submission increments `cur_vmid_cnt` and marks `LPFC_VMID_REQ_REGISTER`; failure removes the hash entry, frees per-CPU storage, and marks the slot free. The inactive VMID timer is enabled once globally through the physical port flag.

## State And Persistence
VMID state is volatile per-vport memory. The `vport->vmid` array stores slots, `vport->hash_table` indexes active slots, `cur_vmid_cnt` tracks allocated entries, and each entry carries flags, the host UUID, VMID length, read/write counters, union tag value, deletion policy, and per-CPU last-I/O timestamps. There is no on-disk persistence; registration state is recreated after link/login reinitialization.

## Dependencies And Integration Points
This file depends on Linux hash tables, percpu allocation, jiffies, rwlocks, DMA direction enums, and LPFC vport/HBA state. It integrates with LPFC SCSI/NVMe I/O build paths through the returned tag, with fabric registration helpers `lpfc_vmid_uvem()` and `lpfc_vmid_cmd()`, with CS_CTL allocation via `lpfc_vmid_get_cs_ctl()`, and with the HBA inactive VMID timer.

## Risks And Edge Cases
The function uses `strlen(uuid)` but compares 16 bytes in the hash lookup and copies `vmid_len` into `host_vmid`; callers must provide a bounded, NUL-terminated UUID representation consistent with the 16-byte storage. Failed registration frees `last_io_time` but does not clear the pointer in the visible code, creating risk if later paths assume NULL before reuse. Hash insertion happens before registration, so all paths must respect `LPFC_VMID_REQ_REGISTER` and `LPFC_VMID_DE_REGISTER`. Per-CPU timestamp updates use `raw_smp_processor_id()`, so preemption assumptions matter.

## Test Signals
Test signals include repeated UUID hits returning tags without extra registration, simultaneous miss races creating only one entry, max-VMID exhaustion returning `-ENOMEM`, QFPA delay returning `-EAGAIN` and setting worker events, registration failure cleanup, inactivity timer start once, app-header and priority-tag modes, vport reinit clearing hash/counters/timestamps, and read/write counter updates by DMA direction.
