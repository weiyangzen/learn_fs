<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_kexec.c -->
# sources/distributed-fs/ceph-client/security/integrity/ima/ima_kexec.c

## Purpose
Carries the IMA measurement list across kexec soft reboots and validates/restores measurement buffers supplied by the previous kernel.

## Important APIs, Types, And Functions
- Under `CONFIG_IMA_KEXEC`: `ima_add_kexec_buffer()`, `ima_kexec_post_load()`, `ima_measure_kexec_event()`, internal allocation/dump/update helpers, reboot notifier.
- Always built restore path: `ima_load_kexec_buffer()`.
- Range validation: `ima_validate_range()`.
- State includes `ima_kexec_file`, `kexec_segment_size`, `ima_kexec_buffer`, and notifier registration flag.

## Control Flow
During kexec file load, IMA sizes a segment for the current binary runtime list plus extra memory, allocates a seq_file buffer, measures a `kexec_load` event, and adds an aligned buffer segment to the kexec image. After load, it maps the segment and registers a reboot notifier. At execute time, the notifier serializes the current measurement list with an `ima_kexec_hdr` into the mapped segment. On next boot, `ima_load_kexec_buffer()` fetches and restores that list, then frees the handoff buffer.

## State And Persistence
The handoff buffer is transient memory passed between kernels. The serialized list and header persist only across the kexec transition. The runtime measurement list remains append-only and is restored into the next kernel's IMA state.

## Dependencies And Integration Points
Depends on kexec image APIs, seq_file serialization from `ima_fs.c`, IMA queue state, reboot notifiers, physical memory validation helpers, architecture page/RAM checks, and `ima_restore_measurement_list()`.

## Risks And Edge Cases
Crash kernels are skipped. Oversized measurement lists are rejected if they approach address limits or consume too much RAM. The segment size cannot change between load and execute. Mapping failures or buffer overflows can prevent restoration and should not corrupt the next kernel.

## Test Signals
Kexec tests should show `ima_kexec` measurement events, populated `image->ima_buffer_*` fields, successful restore logs after soft reboot, correct measurement counts before/after kexec, and warnings for invalid previous-kernel buffer ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/integrity/ima/ima_kexec.c -->
