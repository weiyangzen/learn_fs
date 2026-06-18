<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/hostaudio_kern.c -->
# sources/distributed-fs/ceph-client/arch/um/drivers/hostaudio_kern.c

Purpose: implements UML OSS sound relay devices that proxy guest DSP and mixer operations to host audio device files.

Important APIs/types/functions: state structs are `hostaudio_state` and `hostmixer_state`. Module parameters and boot options configure `dsp` and `mixer`. DSP operations include `hostaudio_read()`, `hostaudio_write()`, `hostaudio_poll()`, `hostaudio_ioctl()`, `hostaudio_open()`, and `hostaudio_release()`. Mixer operations include `hostmixer_ioctl_mixdev()`, `hostmixer_open_mixdev()`, and `hostmixer_release()`.

Control flow: module init registers OSS DSP and mixer devices. Opening a guest audio node opens the configured host path with matching read/write flags. Reads allocate a kernel buffer, read from host, and copy to user. Writes duplicate user data and write it to host. Selected DSP ioctls copy integer arguments through a local variable before forwarding to the host FD; mixer ioctls are forwarded directly.

State and persistence: global `dsp` and `mixer` paths persist for the module lifetime. Each open file stores a host FD in `private_data`. No audio data is persisted by the driver.

Dependencies and integration points: depends on OSS sound registration APIs, UML host `os_open_file`, `os_read_file`, `os_write_file`, `os_ioctl_generic`, kernel parameter locking, and host `/dev/sound/dsp`/`mixer` or configured equivalents.

Risks: OSS interfaces are legacy and host device availability varies. `hostmixer_open_mixdev()` allocates `state` but does not assign `state->fd` before storing `private_data`, which is a correctness risk for ioctl/release. Poll is unimplemented. Large reads/writes allocate buffers proportional to user count.

Test signals: module load/unload, open/read/write DSP, supported DSP ioctls, mixer open/ioctl/release, invalid host paths, concurrent opens while changing module parameters, and large I/O allocation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/hostaudio_kern.c -->
