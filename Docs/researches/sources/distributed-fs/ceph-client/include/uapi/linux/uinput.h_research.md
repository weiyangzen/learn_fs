# sources/distributed-fs/ceph-client/include/uapi/linux/uinput.h

Purpose: Defines the userspace input device creation ABI for `/dev/uinput`.

Important APIs/types/functions: `UINPUT_VERSION` is 5 and names are limited by `UINPUT_MAX_NAME_SIZE`. `uinput_setup` configures input ID, name, and force-feedback capacity. `uinput_abs_setup` configures one absolute axis. Ioctls create/destroy devices, set event/key/relative/absolute/misc/LED/sound/FF/switch/property bits, set physical path, get sysfs name, and get version. Force-feedback upload/erase structs coordinate callback requests. Legacy `uinput_user_dev` supports write-based setup.

Control flow: Userspace opens uinput, sets supported bits, configures setup and axes, calls `UI_DEV_CREATE`, writes input events, handles optional FF upload/erase event/ioctl handshake, then destroys or closes the device.

State and persistence behavior: Virtual input device state is kernel runtime state tied to the file descriptor and created device lifetime. Events affect input subsystem state until released.

Dependencies and integration points: Includes `linux/types.h` and `linux/input.h`; integrates with evdev, input core, force-feedback, sysfs, and compositor/desktop input stacks.

Risks: Partial setup may be applied before an ioctl fails. Incorrect capability bits create misleading devices. FF callbacks block until userspace completes the paired end ioctl.

Test signals: Create devices through modern and legacy flows, configure absolute axes, emit events, read from evdev, verify sysfs name/version, and exercise FF upload/erase handshakes and error paths.
