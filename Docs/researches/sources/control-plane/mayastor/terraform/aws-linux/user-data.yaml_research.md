# sources/control-plane/mayastor/terraform/aws-linux/user-data.yaml

Purpose: cloud-init user data creating an SSH-capable privileged user for AWS/Linux-style Terraform images.

Important APIs/types/functions: creates default user and templated `${ssh_user}` with passwordless sudo, bash shell, groups `users,wheel`, plaintext password `mayastor`, unlocked password, and `${ssh_key}` authorized key. Enables SSH password auth and sets `ec2-user:mayastor`.

Control flow: cloud-init applies users, SSH config, and password changes on first boot.

State/persistence: persists users, password hashes, sudo rights, and authorized keys in the VM.

Dependencies/integration: templated by Terraform variables and paired with metadata seed.

Risks: plaintext default password and `ssh_pwauth: True` are risky outside disposable test environments.

Test signals: provisioned VM should allow SSH with the injected key and passwordless sudo for `${ssh_user}`.
