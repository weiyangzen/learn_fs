<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/config.rb -->
# sources/control-plane/rook/tests/scripts/multi-node/config.rb

Purpose: Vagrant/kubernetes multi-node test configuration values. It defines the base OS, box, node counts, and disk layout used by the multi-node scripts.

Important structure: uses CentOS 7, nine total instances, one etcd, one Kubernetes master, all instances as Kubernetes nodes, and two 20G disks for disk-enabled nodes.

State, persistence, and integration: consumed by the surrounding Vagrant environment to create VM topology and storage. Dependencies include Vagrant config conventions used by the Rook multi-node setup. Risks include old CentOS 7 base image, high local resource demand, and fixed disk sizing. Test signals are successful VM provisioning and availability of disks for Ceph OSD tests.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/config.rb -->
