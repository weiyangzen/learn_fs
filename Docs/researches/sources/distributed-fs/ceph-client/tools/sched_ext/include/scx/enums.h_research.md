# sources/distributed-fs/ceph-client/tools/sched_ext/include/scx/enums.h

Purpose: lightweight user-space wrapper exposing generated sched_ext enum initialization to loaders.

Important APIs/functions: includes `enums.autogen.h`; no independent functions are defined.

Control flow: none in this wrapper.

State and persistence: delegates skeleton enum initialization behavior to the generated header.

Dependencies and integration: included by `common.h`; loaders get `SCX_ENUM_INIT()` through this path.

Risks: wrapper must stay present for include stability even though the generated file carries the implementation.

Test signals: C loaders compile and `SCX_OPS_OPEN()` can call generated enum initialization.
