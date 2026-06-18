# sources/cloud-native/moby/daemon/exec_windows.go

Purpose: Windows-specific exec process option setup.

Important APIs and control flow: `execSetPlatformOpt` checks the target container image platform and, for Windows containers, assigns `p.User.Username = ec.User`. It returns nil without applying Linux-specific capabilities, AppArmor, or rlimit logic.

State, dependencies, and risks: it mutates only the OCI `specs.Process` user field and depends on the daemon container `ImagePlatform.OS`. The file intentionally keeps behavior minimal because Windows user handling is passed through as a username rather than resolved to Linux UID/GID and supplementary groups. Risks are mostly integration-level: non-Windows containers running on a Windows daemon path receive no user mapping here, and invalid usernames are left to lower layers. No tests for this file are included in this group.
