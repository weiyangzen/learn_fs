<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_wrapper.h -->
# sources/distributed-fs/ceph-client/include/net/tc_wrapper.h

Purpose: Provides retpoline-aware wrappers around TC action and classifier indirect calls, replacing common built-in indirect calls with direct calls when safe and falling back to function pointers otherwise.

Important APIs/types/functions: Under `CONFIG_MITIGATION_RETPOLINE`, static keys `tc_skip_wrapper_act` and `tc_skip_wrapper_cls` control whether wrappers are skipped. `TC_INDIRECT_ACTION_DECLARE()` and `TC_INDIRECT_FILTER_DECLARE()` declare indirect-callable action/classifier functions. `tc_act()` checks built-in action function pointers for gact, mirred, pedit, skbedit, skbmod, police, BPF, connmark, csum, ct, ctinfo, gate, MPLS, NAT, tunnel_key, VLAN, IFE, simple, and sample. `tc_classify()` similarly checks BPF, u32, flower, fw, matchall, basic, cgroup, flow, and route4 classifiers. `tc_wrapper_init()` enables skip static keys on x86 without retpoline when more than one built-in target exists. Without retpoline mitigation, wrappers are simple direct pointer calls.

Control flow: Packet classification and action execution call `tc_classify()`/`tc_act()` instead of raw function pointers. The wrapper fast-path compares the operation pointer against built-in functions and calls the direct symbol; if no match or skipping is enabled, it uses the original function pointer.

State and persistence behavior: Only static key state persists globally. No per-action state is stored here.

Dependencies/integration points: Depends on `pkt_cls.h`, CPU feature checks, static keys, and indirect call wrapper support. Integrates all built-in TC classifier/action implementations.

Risks: The wrapper must preserve exact call semantics and config guards. Missing a built-in target only loses optimization, but wrong function comparison or signature mismatch is fatal. Static key enable policy must match CPU retpoline needs.

Test signals: Build matrix for retpoline/non-retpoline and modular/built-in TC actions, packet classifier/action selftests, objdump or ftrace checks for direct-call paths, and runtime tests with static keys toggled by CPU feature.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/net/tc_wrapper.h -->
