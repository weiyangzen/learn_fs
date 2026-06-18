<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/CMakeLists.txt -->
# sources/distributed-fs/lizardfs/src/cgi/CMakeLists.txt

## Purpose
CMake install/configuration definition for LizardFS CGI UI scripts, server wrappers, and static assets.

## Important APIs, Types, and Functions
Uses `configure_file` to generate `mfscgiserv`, `lizardfs-cgiserver`, `chart.cgi`, and `mfs.cgi` from `.in` templates. Defines `CGI_FILES`, `CGI_SCRIPTS`, and `CGI_SERVERS`, then installs static files to `${CGI_SUBDIR}`, scripts to `${CGI_SUBDIR}`, and server programs to `${SBIN_SUBDIR}`.

## Control Flow, State, and Persistence
At configure time, placeholders such as paths and protocol base values are substituted. At install time, static assets and executable scripts become persistent package files.

## Dependencies and Integration Points
Depends on project variables like `CGI_SUBDIR`, `SBIN_SUBDIR`, `CGI_PATH`, `DATA_PATH`, and `PROTO_BASE`. It integrates with RPM service units that run `lizardfs-cgiserver`.

## Risks and Test Signals
Risks include generated scripts lacking executable permissions if install mode/macros are wrong, path substitution mismatches, deprecated `mfscgiserv` still installed, and Python version assumptions. Test signals are configured script shebangs/placeholders, installed execute bits, static asset availability, `chart.cgi` protocol constants, and systemd CGI service serving the installed root.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/cgi/CMakeLists.txt -->
