# sources/cloud-native/ostree/man/ostree-admin-unlock.xml

Purpose: documents `ostree admin unlock`, which makes the current deployment writable for hotfix or development.

Important APIs/types: options `--hotfix` and `--transient`; description focuses on removing the read-only bind mount on `/usr`.

Control flow: changes mount/deployment state so `/usr` can be modified; hotfix semantics persist modifications differently than transient unlock.

State and persistence: mutates live mount state and may create persistent hotfix changes depending on option.

Dependencies and integration: connected to immutable deployment mount setup from `ostree-prepare-root`, admin cleanup/upgrade semantics, and service restarts.

Risks and test signals: high risk because it weakens immutability. Docs must distinguish persistent hotfix from transient development. Signals are unlock/hotfix tests, reboot persistence tests, and mount writability checks.
