# sources/control-plane/mayastor/terraform/mod/libvirt/network_config.cfg

Purpose: netplan network config for libvirt Terraform guests.

Important APIs/types/functions: configures version 2, interface `ens3`, and DHCPv4.

Control flow: consumed by cloud-init/netplan on boot.

State/persistence: persists guest network configuration.

Dependencies/integration: used by libvirt module where the primary NIC is named `ens3`.

Risks: fails on images whose primary interface has a different name.

Test signals: libvirt guest should obtain IPv4 DHCP on `ens3`.
