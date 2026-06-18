# sources/distributed-fs/ceph-client/drivers/net/ethernet/brocade/bna/bfa_defs_mfg_comm.h

Purpose: shared manufacturing and VPD constants/types for BFA/BNA adapters.

Important APIs/types/functions: defines manufacturing block version constants, `BFA_MFG_SERIALNUM_SIZE`, `STRSZ`, card type enum values, `bfa_mfg_is_mezz`, GPIO/card-property mapping macro `bfa_mfg_adapter_prop_init_gpio`, VPD length/header/vendor constants, VPD vendor enum, and packed `struct bfa_mfg_vpd`.

Control flow: most content is declarative, except `bfa_mfg_adapter_prop_init_gpio`, a macro that decodes GPIO strap/card identity into adapter properties and card type. The macro marks prototypes, sets port count and speed property fields, and classifies unsupported/invalid values.

State and persistence behavior: describes persistent manufacturing identity and VPD data stored in adapter flash/NVRAM. `struct bfa_mfg_vpd` contains version/signature/checksum/vendor/length and a 512-byte data array. Consumers copy this into adapter attributes.

Dependencies and integration points: includes `bfa_defs.h`, creating a circular-looking include relationship that is protected by include guards. It expects BFI adapter property macros such as `BFI_ADAPTER_SETP`, `BFI_ADAPTER_PROTO`, `BFI_ADAPTER_TTV`, and `BFI_ADAPTER_UNSUPP` from lower headers included through `bfa_defs.h`/`cna.h`.

Risks: card type and VPD constants must match firmware/manufacturing data. The GPIO macro intentionally falls through from `CB_GPIO_TTV` to two-port 8G handling; accidental `break` changes behavior. `STRSZ` rounds string storage to 4-byte boundaries, so callers must use defined lengths and avoid string overrun assumptions.

Test signals: adapter attribute queries should classify mezzanine cards, prototypes, port count, and speed correctly for known card types. VPD parsing should validate signatures, vendor tags, and length/checksum before display.
