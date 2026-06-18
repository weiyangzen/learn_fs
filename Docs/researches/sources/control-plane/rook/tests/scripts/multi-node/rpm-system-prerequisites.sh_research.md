<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/rpm-system-prerequisites.sh -->
# sources/control-plane/rook/tests/scripts/multi-node/rpm-system-prerequisites.sh

Purpose: installs RPM-based host prerequisites for the multi-node Vagrant/libvirt Rook test environment.

Important APIs and control flow: `install_deps` scrapes the HashiCorp releases index for the latest Vagrant version, installs qemu/libvirt/Ruby/GCC/Docker/Kubernetes client/Go/git dependencies through yum, installs the Vagrant RPM, installs the `vagrant-libvirt` plugin, then starts Docker.

State, persistence, and integration: mutates system packages, Vagrant plugins, and Docker service state. Dependencies include yum, curl, internet access, HashiCorp release page structure, and systemd. Risks include latest-version scraping instability, lack of package pinning, and root-level host changes. Test signals are successful package/plugin install and Docker start.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/scripts/multi-node/rpm-system-prerequisites.sh -->
