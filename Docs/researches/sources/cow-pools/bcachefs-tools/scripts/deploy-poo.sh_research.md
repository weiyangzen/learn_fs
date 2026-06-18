# File Research: sources/cow-pools/bcachefs-tools/scripts/deploy-poo.sh

This Bash script builds and deploys the “Principles of Operation” PDF.

Behavior:
- Uses `set -e`.
- Changes to the repository root relative to the script path.
- Consumes stdin when run as a git hook.
- Runs `make bcachefs-principles-of-operation.pdf`.
- Copies the PDF to `root@evilpiepirate.org:/home/bcachefs/doc/`.
- Runs remote `chown bcachefs:bcachefs` on the deployed PDF.
- Prints the public deployment URL.

Operational notes:
- Can be run directly or symlinked as `.git/hooks/pre-push`.
- Requires SSH access to the deployment host as root.
