## sources/distributed-fs/ipfs-kubo/test/sharness/t0047-add-mode-mtime.sh

Purpose: exhaustive tests for preserving, setting, changing, retrieving, and stat-formatting UnixFS mode and mtime metadata for files, symlinks, and directories.

Important helpers and control flow: `mk_name`, `mk_file`, `mk_dir`, `test_file`, `setup_directory`, `test_directory`, `test_stat_template`, `test_stat`, and `test_all` generate fixtures and run the same matrix over CID/layout modes. The script sets import defaults for deterministic CIDs, checks that metadata flags have no effect unless used, verifies preserve/set options including nanoseconds, tests symlink restrictions, recursively restores directories, and validates `ipfs files stat` templates.

State and dependencies: creates files/directories/symlinks with specific modes and mtimes, stores DAGs, uses an offline daemon, and compares stat/cat/restored filesystem output.

Risks: platform filesystem timestamp precision and symlink metadata support can vary. Test signal is exact mode/mtime preservation, successful recursive restoration, and template output for string/octal/seconds/nanoseconds fields.
