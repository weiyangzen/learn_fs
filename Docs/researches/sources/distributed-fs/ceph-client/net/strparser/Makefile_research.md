# sources/distributed-fs/ceph-client/net/strparser/Makefile

Purpose: Hooks the stream parser implementation into the kernel build.

Important APIs/types/functions: `obj-$(CONFIG_STREAM_PARSER) += strparser.o` builds `strparser.c` when the Kconfig symbol is enabled.

Control flow: Kbuild expands the conditional object list from the configuration. No additional subdirectories or composite objects are involved.

State and persistence behavior: No runtime state. Build output depends solely on `CONFIG_STREAM_PARSER`.

Dependencies and integration points: Integrates with `net/strparser/Kconfig` and the main networking Makefile inclusion chain.

Risks and test signals: Risk is accidental omission or wrong object name causing consumers to fail at link time. Test builds with `CONFIG_STREAM_PARSER=y/m` where supported and with consumers selecting it.
