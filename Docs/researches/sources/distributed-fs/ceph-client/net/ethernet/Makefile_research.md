# sources/distributed-fs/ceph-client/net/ethernet/Makefile

Purpose: Kbuild fragment for the Linux Ethernet layer under this source tree.

Important APIs/entries: declares `obj-y += eth.o`, so `eth.o` is always built into the Ethernet networking layer when this Makefile is reached.

Control flow: the kernel build system reads this Makefile and adds `eth.o` to the built-in object list for the directory. There are no conditionals or module entries here.

State and persistence: no runtime state. Its only effect is build graph configuration.

Dependencies and integration: depends on Kbuild semantics and the presence of `eth.c`/`eth.o` in the same directory. Integrates with parent networking Makefiles that descend into `net/ethernet`.

Risks and test signals: risk is low; accidental removal would break Ethernet helper linkage broadly. Test signal is a successful kernel/networking build and expected inclusion of `eth.o` in built-in objects.
