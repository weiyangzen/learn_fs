# sources/distributed-fs/lizardfs/src/uraft/lizardfs-uraft-helper.in

Purpose: Configured Bash helper used by uRaft to query/promote/demote LizardFS masters and manage floating IP addresses.

Important APIs/types/functions: Functions `load_config`, `lizardfs_master`, `lizardfs_admin`, `get_metadata_version_from_file`, `lizardfs_promote`, `lizardfs_demote`, `lizardfs_quick_stop`, `lizardfs_metadata_version`, `lizardfs_isalive`, `lizardfs_assign_ip`, `lizardfs_drop_ip`, `lizardfs_dead`; command dispatch case.

Control flow: The script loads master and uraft configs, validates floating IP and admin password settings, probes metadata version through `lizardfs-admin` or `mfsmetarestore`, promotes by admin command or disk recovery path, demotes by dropping IP and restarting as shadow, and assigns/drops primary and optional secondary floating IPs.

State and persistence: Reads config files, metadata lock/path state, and metadata version from disk. Mutates service state by restarting `mfsmaster`, stopping/promoting/demoting via admin commands, and adding/removing IP addresses with `sudo ip`.

Dependencies and integration: Depends on installed `mfsmaster`, `lizardfs-admin`, `mfsmetarestore`, `logger`, `getent`, `awk`, `arping`, and system networking. It is called by the uRaft controller command hooks.

Risks and test signals: High operational risk: it manipulates master personality and floating IPs. Config loading uses shell sourcing of filtered config lines, so config content trust matters. Several commands require sudo/network privileges. No direct tests in this subset.
