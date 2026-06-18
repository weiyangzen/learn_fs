# sources/cloud-native/ostree/man/ostree-checkout.xml

Purpose: documents `ostree checkout`, which materializes a commit into a filesystem directory.

Important APIs/types: required `COMMIT`, optional `DESTINATION`; options `--user-mode`, `--subpath`, `--union`, `--union-add`, `--union-identical`, `--whiteouts`, `--process-passthrough-whiteouts`, `--allow-noent`, `--from-stdin`, `--from-file`, `--fsync`, `--require-hardlinks/-H`, `--force-copy-zerosized/-z`, `--force-copy/-C`, `--bareuseronly-dirs/-M`, `--skip-list`, `--selinux-policy`, `--composefs`, and `--composefs-noverity`.

Control flow: resolves the commit, chooses output destination, optionally filters subpaths or batch inputs, then writes tree contents using hardlinks/reflinks/copies with union, whiteout, SELinux, fsync, or composefs behavior.

State and persistence: writes checkout directories or composefs artifacts and may preserve/overwrite existing files depending on union mode.

Dependencies and integration: integrates repository object storage, checkout engine, SELinux labeling, composefs generation, Docker/overlay whiteout handling, and batch interfaces.

Risks and test signals: many option interactions can lose data or alter security labels. Signals are checkout tests for union modes, hardlink requirements, whiteouts, skip lists, SELinux labels, fsync policy, and composefs output.
