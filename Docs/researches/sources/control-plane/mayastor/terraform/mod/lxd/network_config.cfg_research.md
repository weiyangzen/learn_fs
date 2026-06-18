# sources/control-plane/mayastor/terraform/mod/lxd/network_config.cfg

Purpose: netplan network config for LXD Terraform guests/containers.

Important APIs/types/functions: configures version 2, interface `eth0`, and DHCPv4.

Control flow: consumed by cloud-init/netplan on boot.

State/persistence: persists guest/container network configuration.

Dependencies/integration: used by LXD module where the primary interface is `eth0`.

Risks: minimal, but interface naming must match the LXD image/runtime.

Test signals: LXD instance should obtain IPv4 DHCP on `eth0`.
