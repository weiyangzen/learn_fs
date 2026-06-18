# sources/distributed-fs/ceph-client/drivers/s390/char/uvdevice.c

Purpose: misc-device UAPI bridge that lets userspace issue selected s390 Ultravisor calls through validated ioctls when the UV facility is present.

Important APIs/types/functions: defines ioctl-to-UVC support mapping, global `uvdev_info`, `uvio_ioctl`, `uvio_copy_and_check_ioctl`, and handlers `uvio_uvdev_info`, `uvio_attestation`, `uvio_add_secret`, `uvio_list_secrets`, `uvio_lock_secrets`, and `uvio_retr_secret`. Registers misc device `UVIO_DEVICE_NAME`.

Control flow: ioctl entry validates direction/type/number/size, copies `struct uvio_ioctl_cb`, rejects flags/reserved data, dispatches by ioctl number, performs per-command size/address sanity checks, builds the matching UV control block, calls `uv_call` or `uv_call_sched`, stores UV return/reason codes, and copies the ioctl control block back to userspace.

State and persistence: persistent module state is only supported-command metadata and the miscdevice registration. Secret-store effects are persisted inside the Ultravisor, not in this driver. Sensitive retrieved-secret buffers are freed with `kvfree_sensitive`.

Dependencies and integration: depends on `asm/uvdevice.h`, `asm/uv.h`, UV facility detection via `module_cpu_feature_match`, Linux miscdevice and user-copy APIs, vmalloc/kzalloc allocation paths, and UV command availability bits in `uv_info.inst_calls_list`.

Risks: this is a privileged platform ABI surface; validation must prevent kernel memory corruption while leaving semantic UV errors in `uv_rc/uv_rrc`. List-secret loop bounds must not overrun the user buffer. Attestation copies several user-provided buffers and lengths. Retrieve-secret maps a UAPI index and output into one mutable buffer.

Test signals: ioctl ABI tests for all invalid command/type/size/reserved cases, UVDEV_INFO support mask on systems with varying UV command lists, attestation length/address failures, add/list/lock/retrieve secret return-code propagation, and secret-buffer zeroing checks.
