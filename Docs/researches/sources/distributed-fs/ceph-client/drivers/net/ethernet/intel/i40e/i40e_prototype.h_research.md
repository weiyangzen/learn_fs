# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/i40e/i40e_prototype.h

## Purpose

`i40e_prototype.h` is the shared declaration surface for i40e common code. It collects function prototypes that are needed before or outside the standard operations structures, especially AdminQ setup, AdminQ command wrappers, switch/VSI/filter/PHY/DCB/NVM/DDP helpers, hardware reset/common initialization helpers, and firmware/API version predicates. It is a central coupling point between implementation files such as `i40e_common.c`, `i40e_adminq.c`, `i40e_nvm.c`, DDP/profile code, VF/virtchnl handling, and higher-level PF driver code.

## Important APIs, Types, and Functions

- AdminQ lifecycle and command send path: `i40e_init_adminq()`, `i40e_shutdown_adminq()`, `i40e_clean_arq_element()`, `i40e_asq_send_command()`, `i40e_asq_send_command_atomic()`, and `_v2()` with explicit AQ status reporting.
- Firmware/control AdminQ helpers: firmware version, register debug read/write, PHY capabilities/config, link restart/info, driver version send, default VSI, switch config, resource request/release, LLDP/DCB, UDP tunnels, MAC address programming, and port TX suspend/resume.
- VSI/filter/switching helpers: add/update VSI, promiscuous mode variants, VLAN scoped promiscuous controls, VEB operations, MAC/VLAN add/remove v1/v2, cloud filters, control packet filters, and flow-control drop filter helpers.
- NVM surface: `i40e_init_nvm()`, `i40e_acquire_nvm()`, `i40e_release_nvm()`, read buffer/word/module APIs, checksum update/validate, NVM update command dispatch, and wait event clearing.
- Common hardware helpers: shared code init, PF reset, hardware clear, PXE mode clear, link status/update, MAC/PBA reads, PCI config data, queue preconfiguration, filter control, RX control register access, PHY register clause 22/45 access, DDP/profile write/rollback/flash.
- Inline helpers: `i40e_virtchnl_link_speed()` maps `enum i40e_aq_link_speed` to `enum virtchnl_link_speed`; firmware/AdminQ API version helpers compare `hw->aq.*` version fields.

## Control Flow

The header has no runtime control flow beyond inline predicates and link-speed conversion. Its functional role is compile-time orchestration: C files include it to share common entry points without circular dependencies. The inline link-speed conversion uses a switch that returns a virtchnl speed for recognized AdminQ speeds and `VIRTCHNL_LINK_SPEED_UNKNOWN` otherwise. Version helpers use straightforward major/minor comparisons and negate greater-or-equal checks for less-than.

## State and Persistence Behavior

The header itself persists no state, but most prototypes mutate or query `struct i40e_hw`, AdminQ rings, firmware state, switch/VSI state, PHY state, NVM/FLASH, DDP profiles, and adapter registers. Because this declaration surface is broad, signature stability is important: changing parameter ownership, endianness, length units, or status conventions affects many implementation files. The inline helpers read `hw->aq.api_maj_ver`, `api_min_ver`, `fw_maj_ver`, and `fw_min_ver`, so those fields must be initialized before version-gated logic uses them.

## Dependencies and Integration Points

The file includes Linux ethtool declarations, virtchnl definitions from `linux/avf/virtchnl.h`, `i40e_debug.h`, and `i40e_type.h`. It exposes i40e common code to PF driver, VF compatibility paths, AdminQ implementation, NVM update code, DCB/LLDP handling, flow director/filter logic, PHY access, DDP package loading, and ethtool flash paths. It also ties i40e link-speed representation to the virtchnl ABI used when reporting link information to virtual functions.

## Risks

- As a shared header, it can hide large blast radius. A prototype change can silently require updates in several subsystems and out-of-tree users.
- Many AdminQ APIs take raw buffers and lengths. Mismatched byte/word units, endian handling, or lifetime assumptions are not enforced by this header.
- Several operations expose firmware or persistent hardware mutation, especially NVM, PHY, DDP, switch, and MAC/VLAN helpers. Callers must satisfy locking and reset-state preconditions documented in implementation files rather than here.
- Inline version comparisons assume initialized version fields; use before AdminQ discovery could gate features incorrectly.
- The `i40e_virtchnl_link_speed()` mapping must stay aligned with both AdminQ enum values and virtchnl ABI additions.

## Test Signals

Build coverage is the primary signal for this header: all i40e compilation units should compile without prototype drift. Runtime signals include successful AdminQ init/shutdown, link reporting to VFs at every supported speed, firmware/API version-gated features taking expected branches, NVM update paths linking to `i40e_nvm.c`, and DDP/ethtool flash paths resolving declared helpers. Static analysis should focus on raw buffer length handling and mismatched status-code conventions across implementations.
