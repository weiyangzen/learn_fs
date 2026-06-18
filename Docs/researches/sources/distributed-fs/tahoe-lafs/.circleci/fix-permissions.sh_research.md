## sources/distributed-fs/tahoe-lafs/.circleci/fix-permissions.sh

Purpose: prepares CircleCI image filesystem permissions so tests and setup can run as the non-root `nobody` user.

Important behavior: strict Bash mode, accepts wheelhouse path, bootstrap virtualenv path, and project root, changes `nobody` home to `/tmp/nobody`, recursively chowns the project root, creates the wheelhouse, and chowns it to `nobody`.

Control flow: defines `CHOWN_NOBODY` from `id --group nobody`, applies it to project and wheelhouse, and exits on any failure.

State and dependencies: mutates system user metadata with `usermod`, file ownership under the checkout, and wheelhouse directory ownership. Requires root privileges in the image build context.

Risks: recursive chown over the project root can be expensive and broad; incorrect paths could alter unintended files. It is deliberately paired with non-root CI runs that require readable checkout and writable wheelhouse.
