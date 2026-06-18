# sources/distributed-fs/ceph-client/drivers/nvme/host/pr.c

## Purpose

`pr.c` implements the block-layer persistent reservation operations for NVMe namespaces. It translates Linux `pr_ops` requests into NVMe reservation register, acquire, release, and report commands, handles both single namespace disks and multipath namespace-head disks, converts NVMe status values into block persistent-reservation status codes, and parses reservation report payloads back into block-layer key and held-reservation structures.

## Important APIs, types, and functions

- `nvme_pr_ops` is the exported `struct pr_ops` used by the block layer.
- `nvme_pr_type_from_blk` and `block_pr_type_from_nvme` translate between Linux `enum pr_type` and NVMe `enum nvme_pr_type`.
- `nvme_send_ns_head_pr_command` selects an active path under the namespace head SRCU lock and submits the command to the chosen namespace queue.
- `nvme_send_ns_pr_command` submits a command directly for a concrete `struct nvme_ns`.
- `__nvme_send_pr_command` builds the common NVMe command fields and dispatches to namespace-head or namespace submission.
- `nvme_send_pr_command` wraps dispatch and maps completion status through `nvme_status_to_pr_err`.
- Operation implementations are `nvme_pr_register`, `nvme_pr_reserve`, `nvme_pr_preempt`, `nvme_pr_clear`, `nvme_pr_release`, `nvme_pr_read_keys`, and `nvme_pr_read_reservation`.
- `nvme_pr_resv_report` issues reservation report, initially requesting extended data structures and retrying without EDS on host-ID inconsistency.

## Control flow

Block persistent reservation callers enter through `nvme_pr_ops`. Register, reserve, preempt, clear, and release allocate the matching NVMe reservation data structure on the stack, fill current, new, or preempt keys in little-endian form, compute `cdw10` action/type/ignore-key fields, and submit a synchronous NVMe command. Register uses `NVME_PR_CPTPL_PERSIST`, so the registration asks the controller to persist through power loss where supported.

Read operations use reservation report. `nvme_pr_read_keys` allocates a report buffer sized for the caller's requested number of keys, calls `nvme_pr_resv_report`, copies generation and registered controller count, and copies either extended or legacy registration entries into the output key array. `nvme_pr_read_reservation` first obtains the registration count with a small report, allocates an exact buffer, retries if the count changed between reports, then finds the entry with `rcsts` set to identify the holder key and maps the NVMe reservation type back to the block type.

Multipath dispatch uses `nvme_disk_is_ns_head`. For a namespace-head disk, the code takes `head->srcu`, calls `nvme_find_path`, stamps the namespace ID, and submits to that path queue. If no path is available it returns `-EWOULDBLOCK`. For a non-multipath namespace disk, it uses `bd_disk->private_data` as `struct nvme_ns`.

## State and persistence behavior

The file does not maintain long-lived state of its own. It sends commands that mutate controller-side reservation state and registration keys. The persistent behavior requested by this implementation is most visible in `nvme_pr_register`, where `NVME_PR_CPTPL_PERSIST` is set. Read paths allocate temporary report buffers with `kvzalloc` or `kzalloc`, free them before return, and expose only copied generation/key/type results to the block layer.

The state visible to the code is namespace topology state: namespace-head SRCU protection, active path selection, namespace IDs, and request queues. This topology can change concurrently, which is why namespace-head commands run under SRCU and may fail with no available path.

## Dependencies and integration points

The implementation integrates Linux block persistent reservations (`linux/pr.h` and `struct pr_ops`) with NVMe core command submission (`nvme_submit_sync_cmd`), namespace/multipath helpers (`nvme_disk_is_ns_head`, `nvme_find_path`), NVMe reservation data structures, unaligned access helpers for `regctl`, and NVMe status helpers such as `nvme_is_path_error`.

It depends on NVMe target-format structures named `nvmet_pr_register_data`, `nvmet_pr_acquire_data`, and `nvmet_pr_release_data` for command payload layout, and on NVMe reservation report structures for parsing controller responses.

## Risks and edge cases

- Multipath commands can return `-EWOULDBLOCK` if no path is currently selectable; upper layers must retry or surface path failure appropriately.
- Reservation report supports both extended and non-extended formats. Bugs in the fallback path can misparse keys or holder state.
- `nvme_pr_read_reservation` retries when registration count changes, but a highly unstable reservation set can still cause repeated work.
- Unsupported block PR flags are rejected with `-EOPNOTSUPP`; only `PR_FL_IGNORE_KEY` is allowed where implemented.
- Status conversion must preserve reservation conflicts and path failures distinctly. Mapping too much to generic I/O error would make cluster fencing failures harder to diagnose.
- Large `num_keys` values can overflow report-size calculations; the code guards `rse_len > U32_MAX`.

## Test signals

Exercise block PR ioctl paths over normal and multipath NVMe namespaces. Validate register, replace, ignore-key register, reserve, release, clear, preempt, and preempt-and-abort. Verify reservation conflict status, invalid field/opcode mapping, no-path multipath behavior, EDS and legacy reservation report parsing, holder-key reporting, generation changes, and concurrent registration changes during `read_reservation`.
