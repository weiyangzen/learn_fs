# sources/cloud-native/cri-o/contrib/test/ci/ansible.cfg

## Purpose
Ansible configuration tuned for CRI-O CI playbooks.

## Important APIs, Types, and Functions
Sets callbacks, forks=10, smart gathering with network subset, host_key_checking=false, root remote_user, log_path=$ARTIFACTS/main.log, static includes, suppressed warnings/skipped output, retry_files disabled, SSH ControlPersist and pipelining.

## Control Flow
Ansible reads this config before playbooks, shaping connection, logging, callback, and fact behavior.

## State and Persistence
Persists logs under ARTIFACTS/main.log; no other direct state.

## Dependencies
Depends on Ansible version accepting legacy static include and callback_whitelist settings.

## Integration Points
Used by contrib/test/ci playbooks during local/remote CI execution.

## Risks and Edge Cases
Disabling host key checking and warnings favors CI speed over security/diagnostics; deprecated options may drift with Ansible versions; log path requires ARTIFACTS.

## Test Signals
Ansible startup and playbook verbosity/log placement validate this file.
