# sources/distributed-fs/ceph-client/drivers/phy/freescale/phy-fsl-lynx-28g.c

## Purpose
NXP Layerscape Lynx 28G SerDes generic PHY driver. It exposes up to eight Ethernet SerDes lanes, discovers boot-time lane protocols and PLL capabilities, supports runtime switching among SGMII/1000Base-X, 10GBase-R, and USXGMII, controls protocol converters, and periodically recovers lanes that lose CDR lock.

## Important APIs, types, and functions
- `struct lynx_28g_priv` stores MMIO base, PLL/lane arrays, `pcc_lock`, and delayed CDR work.
- `struct lynx_28g_pll` caches reset/control registers and a bitmap of supported lane modes derived from PLL rate.
- `struct lynx_28g_lane` tracks `powered_up`, `init`, lane ID, current mode, and generic PHY.
- `lynx_28g_lane_change_proto_conf()` writes large per-protocol TX/RX equalization, PLL, width, and receiver filter settings.
- `lynx_28g_set_mode()` validates Ethernet submode, halts the lane if needed, disables old converter, remaps PLL/protocol, enables new converter, and restores power.
- `lynx_28g_cdr_lock_check()` runs every second and resets RX when a powered initialized lane loses CDR lock.

## Control flow
Probe maps MMIO, reads both PLL configurations to infer supported modes, creates PHYs either for DT child `phy` nodes or all eight lanes, reads each lane's boot protocol from `LNaPSS`/PCCR, registers an xlate provider, and starts delayed CDR monitoring. `init()` marks a lane managed and powers it off because firmware leaves lanes on. `power_on()` requests TX/RX reset and waits for reset-done bits; `power_off()` issues halt requests and waits for halt completion.

## State and persistence
Runtime state is lane mode, powered/init flags, cached PLL register snapshots, and hardware converter/lane registers. There is no disk persistence. Shared protocol converter registers are protected by `pcc_lock`; delayed work uses each PHY mutex before CDR repair.

## Dependencies and integration points
Depends on generic PHY Ethernet mode APIs, OF/platform MMIO, workqueues, and phandle consumers such as DPAA2 Ethernet MACs. It integrates with firmware-initialized SerDes because it reads initial PSS/PCCR state instead of assuming defaults.

## Risks and test signals
Risks include unbounded busy-wait loops if halt/reset bits never change, limited protocol support compared to defined hardware registers, mode mismatch if firmware PSS encoding changes, and recurring CDR reset churn under marginal links. Test lane creation with and without child nodes, supported/unsupported `phy_set_mode_ext()` submodes, link changes between SGMII/10G/USXGMII, PLL-disabled configurations, and CDR-loss recovery under traffic.
