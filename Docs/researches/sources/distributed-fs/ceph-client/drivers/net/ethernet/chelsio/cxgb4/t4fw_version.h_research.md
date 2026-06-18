# sources/distributed-fs/ceph-client/drivers/net/ethernet/chelsio/cxgb4/t4fw_version.h

Purpose: this small header records the driver-side firmware version policy for Chelsio T4, T5, and T6 adapters. It defines the expected firmware version tuple for each chip generation and the minimum acceptable firmware version tuple used by firmware compatibility checks elsewhere in the Chelsio driver stack.

Important macros: `T4FW_VERSION_MAJOR`, `T4FW_VERSION_MINOR`, `T4FW_VERSION_MICRO`, and `T4FW_VERSION_BUILD` define the packaged or expected T4 firmware version as `1.23.3.0` in hex-coded components. `T4FW_MIN_VERSION_MAJOR`, `T4FW_MIN_VERSION_MINOR`, and `T4FW_MIN_VERSION_MICRO` set T4's minimum acceptable firmware to `1.4.0`. Equivalent T5 and T6 expected versions are also `1.23.3.0`, while their minimum version macros are `0.0.0`, meaning this header does not impose a stricter minimum for those generations in this tree.

Control flow: the file has no runtime control flow. It is included by Chelsio code that formats firmware versions, compares adapter firmware against expected or minimum tuples, and decides whether to warn, reject, or continue with firmware-dependent behavior. Combined with `t4fw_api.h`'s `struct fw_hdr` and `FW_HDR_FW_VER_*` macros, it allows code to compare firmware image headers and live adapter firmware revisions.

State and persistence: this header stores compile-time policy only. The values become persistent in built kernel modules and affect adapter initialization behavior until the module or kernel is replaced. Runtime firmware revision state lives in adapter parameter structures populated from firmware queries, not in this header.

Dependencies and integration points: the file has only include guards and constants, but it is coupled to the Chelsio firmware ABI and firmware files distributed with the kernel or vendor packages. PF and VF paths can surface these values through probe logs, ethtool driver information, or compatibility checks.

Risks: stale constants can cause misleading warnings or failed compatibility checks against real adapter firmware. A too-low minimum version may let code use firmware commands not implemented by older firmware, while a too-high minimum can reject otherwise usable devices. Because the constants are per chip generation, copying a T4 policy to T5/T6 without validating feature availability would be risky.

Test signals: build inclusion should be warning-free. Runtime validation is visible in adapter probe logs, firmware compatibility warnings, and `ethtool -i` output that reports live firmware and TP microcode versions. Compatibility tests should cover T4 minimum-version rejection, current-version acceptance, and T5/T6 behavior when firmware reports older but functional versions.
