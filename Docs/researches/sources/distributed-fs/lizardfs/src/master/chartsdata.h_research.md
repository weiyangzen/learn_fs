# sources/distributed-fs/lizardfs/src/master/chartsdata.h

Purpose: declares the master chart-data module interface.

Important APIs/functions: `chartsdata_memusage()` returns current memory usage sample or zero when unsupported; `chartsdata_init()` initializes chart collection.

Control flow: master init calls `chartsdata_init`; other code can query memory usage.

State and persistence: state owned by implementation; chart data is persisted by `chartsdata.cc`.

Dependencies and integration: included by master modules needing memory/metrics initialization.

Risks: small interface hides platform-dependent behavior behind `chartsdata_memusage`.

Test signals: no direct tests in this subset.
