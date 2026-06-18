## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_tc_flower.c

### Purpose
`sparx5_tc_flower.c` translates TC flower filters into Sparx5 VCAP rules. It parses supported dissector keys, validates action combinations and chain progression, selects VCAP keysets, programs actions for trap/mirror/redirect/VLAN/goto/accept, manages PSFP resources for gate and police actions, supports template keyset changes, and reports counters.

### Important APIs, Types, And Functions
The public entry is `sparx5_tc_flower()`. Major internal structures are `sparx5_wildcard_rule`, `sparx5_multiple_rules`, and `sparx5_tc_flower_template`. Important functions include dissector handlers, `sparx5_tc_flower_action_check()`, `sparx5_tc_select_protocol_keyset()`, extra rule copy helpers, chain link helpers, PSFP parse/setup/free helpers, action builders, `sparx5_tc_flower_replace()`, destroy/stats handlers, and template create/destroy handlers.

### Control Flow
Replace validates actions, allocates a VCAP rule for the TC chain, parses supported flower keys, adds a counter and any chain target key, then walks actions. Gate and police actions are parsed into PSFP structures and later allocate stream gate, flow meter, stream filter, and ISDX action if the chip supports PSFP. Other actions immediately add VCAP action fields. The rule then uses a stored template keyset if present; otherwise it intersects rule-required keysets with port-supported keysets, possibly producing multiple wildcarded rules for `ETH_P_ALL`. The rule is validated and added, with extra rules added for remaining keysets.

### State, Persistence, And Dependencies
State persists in VCAP rule storage, per-port `tc_templates`, hardware counters, PSFP pools/hardware, and ISDX mappings. The destroy path repeatedly deletes all VCAP rules with the same cookie and frees PSFP resources from the first rule. Dependencies include VCAP API/client helpers, `vcap_tc` generic flower parsers, `sparx5_vcap_impl`, PSFP helpers, TC gate/police action formats, and netlink extack reporting.

### Integration Points
`sparx5_tc.c` dispatches clsflower setup here. Matchall goto rules can enable VCAP lookups that flower chains then populate. PSFP integrates with `sparx5_psfp.c`, policer/SDLB code, and QoS time. VCAP templates alter port keyset configuration through `sparx5_vcap_set_port_keyset()`.

### Risks
Action ordering and chain validation are strict: non-last chains must end in goto. PSFP allocation is not fully transactional; failures after partial gate/meter allocation can leak until destroy unless VCAP/TC cleanup runs. Template destroy initializes `err = -ENOENT` and never sets it to success after removing a template. Multiple rules for one cookie rely on insertion/order assumptions for resource cleanup.

### Test Signals
Test every supported dissector key, unsupported key detection, fragment flag mapping, action conflict rejection, goto chain validation, trap/mirror/redirect/VLAN actions per VCAP type, PSFP gate/police add and destroy, ETH_P_ALL multi-keyset expansion, counter stats, template create/destroy, and cleanup after mid-replace errors.
