# sources/distributed-fs/ceph-client/drivers/net/dsa/sja1105/sja1105_vl.h

Purpose: this header exposes the optional SJA1105 virtual-link offload API to the rest of the SJA1105 driver. It declares redirect, delete, gate, and stats helpers when `CONFIG_NET_DSA_SJA1105_VL` is enabled and returns extack-backed `-EOPNOTSUPP` stubs otherwise.

Important APIs, types, and functions: `sja1105_vl_redirect()` handles routing-style VL actions, `sja1105_vl_delete()` removes a rule from a port, `sja1105_vl_gate()` accepts tc-gate timing data and creates time-triggered VL state, and `sja1105_vl_stats()` reports hardware drop/error counters through `flow_stats`. Parameters include `struct sja1105_private`, ingress port, rule cookie, `struct sja1105_key`, destination port mask, gate index, priority, base/cycle time, and action gate entries.

Control flow: flow-block parsing code in the main SJA1105 driver can call these helpers without open-coding config guards. Enabled helpers mutate rule/static-config state and may trigger scheduling rebuilds; disabled helpers only set "Virtual Links not compiled in" in `netlink_ext_ack`.

State and persistence: this header does not own state. It defines the API that mutates `priv->flow_block.rules`, `priv->static_config`, and `priv->tas_data.gating_cfg` in the C implementation.

Dependencies and integration points: it includes `sja1105.h`, which supplies private driver state, rule/key types, DSA context, and flow stats types. It is used by tc flower/gate offload paths and by removal/reload logic.

Risks: callers must treat the enabled helpers as transactional only to the extent implemented by `sja1105_vl.c`; failures can occur after partial rule creation and need correct unwinding. The disabled stubs make feature absence visible to user space but still compile callers, so tests need both config variants.

Test signals: build with VL enabled and disabled, verify extack messages for disabled builds, exercise all four helper calls from tc offload paths, and ensure rule deletion and stats collection behave consistently after config reloads.
