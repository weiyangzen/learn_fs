## sources/distributed-fs/ipfs-kubo/test/sharness/t0021-config.sh

Purpose: comprehensive shell coverage for `ipfs config`, `config show`, `config replace`, and `config profile apply`.

Important helpers and control flow: `test_config_cmd_set` validates setting scalar and JSON config values; `test_profile_apply_revert` verifies profile application and inverse profile restoration; `test_profile_apply_dry_run_not_alter` ensures dry-run output does not mutate config; `test_config_cmd` orchestrates config show, replace, identity privacy, addr filters, backup creation, profile output, and daemon-running behavior. The script launches a daemon near the end to verify config commands while online.

State and dependencies: mutates `.ipfs/config`, creates backups, reads real config files, and compares JSON/text output. Depends on jq-like config behavior through the CLI, shell comparisons, and daemon helpers.

Risks: exact config output, private key redaction, and profile side effects are high-value but brittle to config schema changes. Test signals include successful writes, no PrivKey leakage in show/dry-run, replacement rejection when private keys are included, backup files, and daemon-safe config reads.
