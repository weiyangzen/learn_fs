# sources/distributed-fs/ceph-client/drivers/media/firewire/Makefile

Purpose: Build rules for the FireDTV FireWire DVB driver.

Important APIs/types/functions: `obj-$(CONFIG_DVB_FIREDTV) += firedtv.o` declares the composite module. `firedtv-y` includes `firedtv-avc.o`, `firedtv-ci.o`, `firedtv-dvb.o`, `firedtv-fe.o`, and `firedtv-fw.o`; `firedtv-$(CONFIG_DVB_FIREDTV_INPUT)` conditionally adds `firedtv-rc.o`.

Control flow: Kbuild links the listed objects into one `firedtv` module or built-in object according to Kconfig. Remote-control code is compiled only when input support is enabled.

State and persistence: No runtime state. The object list defines link-time feature composition.

Dependencies/integration: Consumes symbols from the FireDTV source files and Kconfig symbols. The base objects share `firedtv.h` internal APIs.

Risks and test signals: Build with and without `CONFIG_DVB_FIREDTV_INPUT`, and ensure every cross-file symbol remains present in the selected object set. Missing `firedtv-rc.o` must be covered by inline stubs in `firedtv.h`.
