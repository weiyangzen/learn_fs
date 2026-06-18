# sources/cloud-native/ostree/man/ostree-admin-set-origin.xml

Purpose: documents `ostree admin set-origin`, which creates/updates a remote and changes a deployment origin used for upgrades.

Important APIs/types: required `REMOTENAME URL` and optional `BRANCH`; options `--set=KEY=VALUE` and `--index=INDEX`.

Control flow: adds remote if needed, applies remote config options, and rewrites the selected deployment's origin file/ref tracking target.

State and persistence: mutates repo remote configuration and deployment origin metadata.

Dependencies and integration: drives future `ostree admin upgrade` behavior; integrated with remotes and deployment indices.

Risks and test signals: risks include changing the wrong deployment origin or remote settings. Signals are origin file inspection, upgrade tracking tests, and remote config tests.
