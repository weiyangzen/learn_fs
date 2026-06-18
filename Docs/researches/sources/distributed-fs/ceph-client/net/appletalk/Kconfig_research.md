# sources/distributed-fs/ceph-client/net/appletalk/Kconfig

Purpose: declares `CONFIG_ATALK`, the AppleTalk protocol stack option.

Important APIs, types, and functions: the single symbol is `config ATALK`, a tristate user-visible option labeled "Appletalk protocol support". It selects `LLC`, enabling the lower link-layer support AppleTalk over Ethernet requires.

Control flow: when selected as built-in or module, Kbuild includes the AppleTalk directory through the top-level net Makefile. The help text describes EtherTalk and LocalTalk support, the required netatalk userspace package, and the module name `appletalk`.

State and persistence: the chosen tristate value persists in `.config` and determines whether the C files in `net/appletalk/` are compiled. Runtime state is created only by the compiled module.

Dependencies and integration points: sourced by `net/Kconfig` under `if NET`. It indirectly controls `aarp.c`, `ddp.c`, and optional proc/sysctl companion files through the AppleTalk Makefile. The `LLC` selection integrates with SNAP/LLC datalink registration used by AARP and DDP.

Risks: AppleTalk code is init-net only in the researched implementation, so enabling it in network-namespace-heavy systems does not imply per-netns support. Since the option selects LLC, dependency changes can alter build surface beyond AppleTalk itself.

Test signals: Kconfig tests should verify `ATALK=m` builds `appletalk.ko`, `LLC` is selected, and toggling `PROC_FS`/`SYSCTL` changes companion object inclusion without hiding the base protocol option.
