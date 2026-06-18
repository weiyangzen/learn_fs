<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/admin/CMakeLists.txt

## Purpose
CMake build definition for the `lizardfs-admin` command-line tool and its legacy `lizardfs-probe` symlink.

## Important APIs, Types, and Functions
Uses project macros `collect_sources`, `create_unittest`, and `link_unittest`. Builds `lizardfs-admin-lib` from collected admin sources, links it with `mfscommon`, builds `lizardfs-admin` from `${LIZARDFS_ADMIN_MAIN}`, and creates an `ALL` custom target `lizardfs-probe` using `ln -sf lizardfs-admin lizardfs-probe`.

## Control Flow, State, and Persistence
Configuration collects source/test lists, build creates the library and executable, test macros create a unit-test target, and install copies the executable plus generated symlink into `${BIN_SUBDIR}`. The symlink is persistent in the build tree and install tree.

## Dependencies and Integration Points
Depends on project CMake helper macros, `mfscommon`, and Unix `ln`. It integrates all `src/admin` command implementation files into one binary and preserves compatibility for callers using `lizardfs-probe`.

## Risks and Test Signals
Risks include `ln -sf` portability on non-Unix generators, source collection relying on project naming conventions, and symlink install behavior on platforms without symlink support. Test signals are successful build of `lizardfs-admin-lib`, unit target linking against `mfscommon`, installed executable, installed `lizardfs-probe` symlink, and command dispatch through both names.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/CMakeLists.txt -->
