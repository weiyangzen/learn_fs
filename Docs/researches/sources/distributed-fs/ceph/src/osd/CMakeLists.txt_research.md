# sources/distributed-fs/ceph/src/osd/CMakeLists.txt

## Purpose
`src/osd/CMakeLists.txt` defines the static `osd` library build composition for the Ceph OSD subsystem. It lists OSD, PG, scrubber, scheduler, EC, tracing, objecter/striper, and performance metric sources, then wires conditional tracing and runtime object-class dependencies.

## Important APIs, Types, and Control Flow
The file defines `osdc_osd_srcs`, conditionally enables GCC `-finstrument-functions` with exclusions for SIMD helper names, and defines `osd_srcs`. `add_library(osd STATIC ${osd_srcs})` creates the target. `target_link_libraries()` exposes `dmclock::dmclock` and `Boost::MPL` publicly and links internal options, objectstore, profilers, fmt, and dl libraries privately. Conditional `add_dependencies()` attach LTTng, eventtrace, and cyg-profile tracepoint generation.

## State and Persistence Behavior
There is no runtime state. Build state is expressed through target sources, link dependencies, compile options, and generated tracepoint dependencies. Object class libraries are declared as runtime dependencies so OSD builds bring in `libcls_*` modules needed for class execution.

## Dependencies and Integration Points
It integrates the classic and newer EC implementations (`ECBackend.cc` and `ECBackendL.cc`), scrubber components, objecter client code, manager OSD perf metric types, class handler support, and optional CephFS/RBD/RGW class libraries.

## Risks and Test Signals
Risks include duplicate or missing source entries, instrumentation flags leaking globally through `add_compile_options`, case mismatch in `set_source_files_properties(osdcap.cc)` versus `OSDCap.cc`, and forgotten runtime class dependencies when new object classes are added. Test signals include clean CMake configure/builds across feature combinations (`WITH_LTTNG`, `WITH_EVENTTRACE`, `WITH_OSD_INSTRUMENT_FUNCTIONS`, `WITH_CEPHFS`, `WITH_RBD`, `WITH_RADOSGW`) and link verification for dynamic class loading.
