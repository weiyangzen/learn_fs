
# sources/distributed-fs/ceph-client/drivers/hwtracing/stm/p_basic.c

Purpose: basic STM framing protocol driver for compatibility with older STM setups.

Important APIs/types/functions: `basic_write()` sends payload data through `stm_data_write()` with timestamp on the first packet, then emits a FLAG packet. `basic_pdrv` registers protocol name `p_basic`.

Control flow: module init registers the protocol with the STM core; exit unregisters it. STM policies without explicit protocol fall back to `p_basic` if available. Writes use the assigned master/channel plus optional channel offset.

State and persistence: no per-output private state. Protocol registration lives in the STM core list while module is loaded.

Dependencies and integration: depends on STM protocol registration and hardware `packet()` callbacks.

Risks: no metadata beyond STP framing and final FLAG, so consumers need only STP decoding but lose richer identification. Write errors before FLAG leave an incomplete frame.

Test signals: create policy using `p_basic`, write from char device and sources, verify timestamped first packet and trailing FLAG, unload protocol after policy unbind.
