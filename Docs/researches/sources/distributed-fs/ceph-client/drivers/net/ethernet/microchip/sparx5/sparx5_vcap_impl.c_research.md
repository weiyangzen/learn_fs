# Research: sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_vcap_impl.c

## Purpose
`sparx5_vcap_impl.c` is the Sparx5 hardware backend for the common Microchip VCAP rule API. It declares the Sparx5 VCAP instance layout, allocates per-instance `vcap_admin` objects, maps hardware blocks, initializes TCAM/action/counter ranges, programs per-port key selection, and supplies callback operations for validation, default rule fields, cache read/write, hardware update, rule moves, and debugfs port information.

## Important APIs, Types, and Functions
- `sparx5_vcap_inst_cfg[]` describes three IS0/CLM instances, two IS2 instances, one ES0 instance, and one ES2 instance with chain ID ranges, lookup counts, block mappings, and ingress/egress direction.
- Public entry points: `sparx5_vcap_init()`, `sparx5_vcap_deinit()`, `sparx5_vcap_get_port_keyset()`, `sparx5_vcap_set_port_keyset()`, and `sparx5_vcap_is_known_etype()`.
- `sparx5_vcap_ops` connects Sparx5 to the common API callbacks.
- Validation/default-field helpers choose keysets and add implicit ingress/egress port masks plus lookup-first bits.
- Cache helpers move rule streams between `admin->cache` and hardware data registers for IS0/IS2 super VCAP, ES0, and ES2.
- Update/move helpers issue VCAP commands and wait for completion through `read_poll_timeout()`.
- Port key selection/deselection helpers enable or disable lookups and set initial selector modes for all front ports.

## Control Flow
Initialization allocates `struct vcap_control`, installs the generated model and operations, then iterates over platform VCAP instance config. For each instance it allocates a `vcap_admin`, initializes lists and cache buffers, maps hardware blocks/cores, initializes the valid address range, programs per-port key selection for the first instance of each type, and adds the admin to the control list. Finally it registers global and per-port debugfs entries.

At rule insertion/update time the generic VCAP API calls back into this file. Validation reads the current per-port key selectors and checks whether the requested keyset can be produced for the rule chain and L3 protocol. Default-field insertion adds the device port as an implicit match and sets lookup selectors. Encoding then uses the generated model to fill cache streams; the backend writes those streams to hardware cache registers and triggers write/read/initialize/move commands for the selected VCAP address.

Deinitialization walks all admins, disables per-port lookup selection, deletes rules through the VCAP core, removes each admin from the list, frees cache streams, and frees the control object.

## State and Persistence Behavior
Driver-owned runtime state lives in `sparx5->vcap_ctrl`, each `vcap_admin` list/rule/cache/address range, and hardware key selection registers. Rule content and counters persist in device VCAP memories while the driver is active. The in-memory cache is transient scratch space. ES0 counters are mirrored through XQS ESDX counters under `queue_stats_lock`, while IS2 and ES2 counters use stage-specific counter tables plus sticky counter registers. There is no disk persistence.

## Dependencies and Integration Points
The file depends on the generated Sparx5 model, shared VCAP API/client/debugfs interfaces, Sparx5 register definitions, netdevice private data, Ethernet protocol constants, mutexes, list handling, and debugfs. It integrates with tc offload via the common VCAP API, with Sparx5 platform constants through `sparx5->data->consts`, with debugfs through `vcap_debugfs()`/`vcap_port_debugfs()`, and with hardware stats through XQS and ACL/EACL counter registers.

## Risks and Edge Cases
- `sparx5_vcap_init()` returns immediately on allocation failure without freeing earlier admins/control, so failure injection should check for leaks.
- The `read_poll_timeout()` waits do not surface timeout status; callers cannot tell if hardware failed to complete an operation.
- Keyset selector changes are broad per port/protocol/lookup and can affect existing rules that depend on previous selector modes.
- Counter index masking (`0xfff` for IS2, `0x7ff` for ES2) can hide out-of-range callers and alias counters if address accounting is wrong.
- `VCAP_SEL_ALL` cache writes are explicitly rejected, so generic API callers must split entry/action/counter writes correctly.
- Debugfs port callbacks are part of the operations table even when debugfs compiles to a no-op stub.

## Test Signals
- Probe/remove tests should validate init/deinit, block mapping, lookup enablement, rule cleanup, and memory cleanup on every failure point.
- VCAP KUnit or mocked-register tests should cover keyset validation for IS0, IS2, ES0, ES2 and unknown ethertypes.
- Hardware tests should insert, update, move, read back, and delete rules across all VCAP stages and verify counters.
- tc-flower tests should verify default port scoping and lookup-first behavior for first and second lookup chains.
- Fault tests should simulate VCAP update timeout and allocation failures.
