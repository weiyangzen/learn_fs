# sources/control-plane/mayastor/terraform/aws-linux/meta-data.yaml

Purpose: cloud-init metadata for an AWS/Linux-style local image instance.

Important APIs/types/functions: sets `instance-id: id-0`, `local-hostname: amz-linux`, and DHCP config for `eth0`.

Control flow: no executable flow; cloud-init consumes it during instance boot.

State/persistence: becomes instance metadata and network configuration for the booted VM.

Dependencies/integration: paired with `user-data.yaml` in Terraform image provisioning.

Risks: static instance ID/hostname can collide if multiple instances share the same seed data.

Test signals: VM should boot with hostname `amz-linux` and DHCP networking on `eth0`.
