## sources/distributed-fs/tahoe-lafs/.circleci/prepare-image.sh

Purpose: orchestrates all CircleCI image preparation steps for permissions, virtualenv creation, and wheelhouse population.

Important behavior: strict Bash mode, takes wheelhouse path, bootstrap virtualenv, project root, and Python executable. It calls `fix-permissions.sh`, then runs `create-virtualenv.sh` and `populate-wheelhouse.sh` as `nobody` via `sudo --set-home`.

Control flow: it sequences privileged ownership setup before non-root Python setup, ensuring the later test user owns or can access generated artifacts.

State and dependencies: mutates project/wheelhouse permissions, creates a virtualenv, and fills the wheelhouse. Depends on all three helper scripts, `sudo`, and the target user.

Risks: failures in any child script abort image prep. The script assumes it is run from an image build context where root can sudo to `nobody`; this may not work unchanged in local shells.
