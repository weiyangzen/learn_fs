## sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/sparx5/sparx5_port.c

### Purpose
`sparx5_port.c` is the main port hardware programming file. It handles link status decoding, speed/interface validation, safe port disable/flush, SerDes setup, PCS and MAC configuration for low-speed and Base-R devices, muxing, flow control, VLAN tag awareness, forwarding urgency, and per-port QoS classification/rewrite programming.

### Important APIs, Types, And Functions
Exports include `sparx5_get_port_status()`, `sparx5_serdes_set()`, `sparx5_port_mux_set()`, `sparx5_port_fwd_urg()`, `sparx5_port_pcs_set()`, `sparx5_port_config()`, `sparx5_port_init()`, `sparx5_port_enable()`, `sparx5_port_qos_set()` and its PCP/DSCP helpers, and `sparx5_get_internal_port()`. Internal control helpers include `sparx5_port_disable()`, `sparx5_port_flush_poll()`, `sparx5_dev_switch()`, `sparx5_port_pcs_low_set()`, `sparx5_port_pcs_high_set()`, and `sparx5_port_config_low_set()`.

### Control Flow
Status reads dispatch on current `port->conf.portmode`: 1G/2.5G PCS paths decode SGMII or Clause 37 words, while Base-R paths inspect high-speed MAC sticky status. Reconfiguration first validates speed and interface compatibility, optionally configures RGMII through chip ops, programs MAC speed/duplex registers for low-speed modes, applies flow control, sets DSM watermarks, and enables QFWD forwarding with a speed-derived urgency. PCS reconfiguration safely disables the active hardware device, switches between low/high-speed device mappings when necessary, programs SerDes and PCS, toggles counter collection, and saves `port->conf`.

### State, Persistence, And Dependencies
State is both hardware-resident and cached in `struct sparx5_port` (`conf`, VLAN tag settings, signal-detect settings, QoS config inputs). Disable/flush manipulates QFWD, HSCH, QSYS, DSM, DEV2G5, DEV10G, PCS10G, and DEV25G registers. Dependencies include Linux PHY/SerDes APIs, DCB constants, generated register macros, chip ops for port capabilities and RGMII, and global constants in `sparx5_main.h`.

### Integration Points
Phylink uses this file for PCS config, link-up MAC config, and link status. Netdev open/stop uses `sparx5_port_enable()` and SerDes power state. VLAN, QoS, PTP, and switchdev behavior depend on the tag, timestamp, and forwarding settings programmed here.

### Risks
The disable sequence is long and hardware-order-sensitive; missed flush completion can leave queues or MAC domains inconsistent. Speed validation has chip-family-specific capability assumptions. Multiple functions save `port->conf`, so callers must understand whether PCS-only or MAC config is being updated. QoS DSCP/PCP maps are global or per-port depending on register block, so per-port APIs may affect broader state.

### Test Signals
Use hardware/register tests for every supported interface and speed, link-down sticky clearing, PCS low/high transitions, QSGMII muxing, SerDes reset/power sequencing, queue flush timeout, pause TX/RX behavior, VLAN tag awareness, port enable/disable, and PCP/DSCP classification and rewrite tables.
