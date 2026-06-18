## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_police.c

### Purpose
`sparx5_police.c` programs Sparx5 service policer hardware for PSFP flow meters. It converts software rate/burst parameters into SDLB token and threshold registers.

### Important APIs, Types, And Functions
The public function is `sparx5_policer_conf_set()`, dispatching on `struct sparx5_policer::type`. The implemented type is `SPX5_POL_SERVICE`, handled by `sparx5_policer_service_conf_set()`. It uses `sparx5_sdlb_pup_token_get()` and `ops->get_sdlb_group()`.

### Control Flow
For service policers, the code retrieves the SDLB group metadata, converts kbit rate to bit/s, computes current and maximum PUP tokens for the group interval, derives burst threshold in group minimum-burst units, and writes token, max-token, and threshold fields in `ANA_AC_SDLB_*` registers. Unknown policer types currently return success without programming.

### State, Persistence, And Dependencies
Policer state persists in hardware SDLB registers indexed by `pol->idx` and group zero subindex. Software state is carried by `struct sparx5_policer`. Dependencies include SDLB group definitions, generated ANA_AC register macros, and chip ops.

### Integration Points
`sparx5_psfp.c` uses this file when adding or deleting flow meters from TC flower police actions. The programmed policer is linked into SDLB groups by `sparx5_sdlb_group_add()` or removed by `sparx5_sdlb_group_del()`.

### Risks
Unsupported policer types silently succeed, which can hide caller mistakes. Rate/burst unit conversions must remain aligned with TC flower parsing and SDLB group initialization. Register programming assumes the caller has selected an appropriate group and index.

### Test Signals
Test police add with representative rates/bursts, zero rate deletion path via PSFP, group max-token calculation, threshold rounding, maximum rate rejection in TC flower, and unknown type behavior.
