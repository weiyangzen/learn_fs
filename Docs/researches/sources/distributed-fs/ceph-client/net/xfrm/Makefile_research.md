# sources/distributed-fs/ceph-client/net/xfrm/Makefile

Purpose: This Makefile maps XFRM Kconfig symbols to object files. It defines the core object set for `CONFIG_XFRM`, feature modules for algorithms, user ABI, compatibility, IPComp, xfrm interfaces, IP-TFS, ESP-in-TCP, and BTF helper objects.

Important build rules: `obj-$(CONFIG_XFRM)` includes `xfrm_policy.o`, `xfrm_state.o`, `xfrm_hash.o`, `xfrm_input.o`, `xfrm_output.o`, `xfrm_sysctl.o`, `xfrm_replay.o`, `xfrm_device.o`, and `xfrm_nat_keepalive.o`. `xfrm_interface-$(CONFIG_XFRM_INTERFACE)` contributes `xfrm_interface_core.o`, with `xfrm_interface_bpf.o` included only when the interface and BTF debug-info configuration match built-in or module mode. Feature symbols add `xfrm_algo.o`, `xfrm_user.o`, `xfrm_compat.o`, `xfrm_ipcomp.o`, `xfrm_iptfs.o`, and `espintcp.o`.

Control flow and integration: The build graph matters because many files register callbacks at init time: `xfrm_iptfs.o` registers mode callbacks, `xfrm_interface.o` registers rtnl/protocol/BPF hooks, and `xfrm_compat.o` registers the translator. Core XFRM always includes NAT keepalive support, even though keepalives activate only when states carry intervals.

State and persistence: No runtime state is persisted here; it shapes compiled objects and module boundaries. The composite `xfrm_interface.o` module conditionally contains BPF kfunc registration depending on BTF.

Risks: The conditional BPF object logic is sensitive to built-in vs module mode. Missing `xfrm_interface_bpf.o` silently removes TC-BPF kfunc support, while including it without BTF support would break build or registration assumptions. Adding core dependencies must account for built-in and modular link order.

Test signals: Build with `CONFIG_XFRM_INTERFACE=y` and `m`, with `CONFIG_DEBUG_INFO_BTF` and `CONFIG_DEBUG_INFO_BTF_MODULES`. Confirm generated modules export expected aliases (`xfrm`) and that `objdump`/`modinfo` includes IP-TFS, IPComp, or ESP-in-TCP only when selected.
