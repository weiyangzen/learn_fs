<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/build-aux/vc-list-files -->
## sources/cloud-native/ostree/build-aux/vc-list-files

### Purpose
This gnulib helper script lists version-controlled files for one or more directories across several VCS backends.

### APIs, Types, and Control Flow
It supports `--help`, `--version`, and `-C SRCDIR`. For each directory, it detects `.git`, `.hg`, `.bzr`, CVS, or `.svn`, then emits relative file paths using the corresponding VCS command. The git path uses `git ls-tree -r HEAD:"$dir"` and filters regular-file entries; other backends use `hg locate`, `bzr ls`, `cvsu` or `awk` over CVS entries, and `svn list -R`.

### State, Dependencies, and Integration
It reads VCS metadata and writes only stdout/stderr. It integrates with maintainer checks and `cfg.mk` exclusion rules.

### Risks and Test Signals
The script uses `eval` to compose pipelines, so quoting is inherited from old gnulib conventions and should not be extended casually. Git symlinks are intentionally ignored. Test signal is correct file listing under git for maintainer rules.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/build-aux/vc-list-files -->
