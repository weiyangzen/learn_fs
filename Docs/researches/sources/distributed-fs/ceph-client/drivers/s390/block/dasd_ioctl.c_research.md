# sources/distributed-fs/ceph-client/drivers/s390/block/dasd_ioctl.c

Purpose: implements the DASD block-device ioctl surface for administrative actions, formatting, format checking, ESE space release, copy-pair swap, profiling, CMB data, API version reporting, and exported DASD information.

Important APIs/types/functions: `dasd_ioctl()` dispatches `BIODASD*` and `DASDAPIVER` commands; helpers cover enable/disable, quiesce/resume, `abortio`/`allowio`, `dasd_format()`, `dasd_check_format()`, `dasd_ioctl_release_space()`, `dasd_ioctl_copy_pair_swap()`, profile reset/read, `__dasd_ioctl_information()`, `dasd_set_read_only()`, `dasd_ioctl_readall_cmb()`, and exported `dasd_biodasdinfo()`.

Control flow: ioctls first resolve the `dasd_device` from the gendisk and then enforce capability, whole-disk, readonly, and user-buffer checks as needed. Most operations delegate to discipline callbacks. Disable deliberately lowers the target state to `BASIC` so `dasdfmt` can still issue format I/O. Information paths combine discipline data with ccw identifiers, state, open counts, and queue length.

State and persistence behavior: quiesce/resume adjust stop bits, abort/allow toggles `DASD_FLAG_ABORTALL`, disable changes target state and disk capacity, formatting and ESE release can mutate media, copy-pair swap mutates copy relation state, readonly changes devmap features unless hardware readonly blocks it, and profiling ioctls read/reset in-memory counters.

Dependencies and integration points: depends on DASD discipline callbacks, Linux block ioctl conventions, `CAP_SYS_ADMIN`, ccw/CMB APIs, `copy_{to,from}_user()`, partition detection consumers via exported `dasd_biodasdinfo()`, and userspace tools such as `dasdfmt`.

Risks and test signals: user pointer and partition rejection paths are security-sensitive. `dasd_release_space()` uses `if (!device->discipline->is_ese && !device->discipline->is_ese(device))`, which risks a NULL callback call and looks intended to be an OR-style guard. Test privileged/unprivileged callers, partition vs whole disk, readonly media, malformed reserved copy-pair data, profile-disabled builds, CMB size variants, and ESE/non-ESE devices.
