<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Makefile -->
# sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Makefile

Purpose: builds the Bluetooth RFCOMM protocol module from its core, socket, and optional TTY sources.

Important APIs/types/functions: `obj-$(CONFIG_BT_RFCOMM) += rfcomm.o` creates the RFCOMM built-in/module target. `rfcomm-y := core.o sock.o` always includes protocol/session and socket support. `rfcomm-$(CONFIG_BT_RFCOMM_TTY) += tty.o` conditionally adds TTY emulation.

Control flow: kbuild expands the object list according to Kconfig. If `CONFIG_BT_RFCOMM=m`, the combined `rfcomm.ko` includes the selected objects; if built-in, objects link into the kernel image.

State and persistence behavior: no runtime state; it controls build composition only.

Dependencies and integration points: aligns with `rfcomm/Kconfig`, module init/exit in `core.c`, socket init/cleanup in `sock.c`, and optional TTY init/cleanup in `tty.c`.

Risks: object ordering matters because `core.o` module init calls socket and TTY init functions; missing `tty.o` when `CONFIG_BT_RFCOMM_TTY` is enabled would break symbols, and including it when disabled would expose unwanted TTY code.

Test signals: build matrix for `CONFIG_BT_RFCOMM` disabled/built-in/module and `CONFIG_BT_RFCOMM_TTY` on/off catches composition errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/net/bluetooth/rfcomm/Makefile -->
