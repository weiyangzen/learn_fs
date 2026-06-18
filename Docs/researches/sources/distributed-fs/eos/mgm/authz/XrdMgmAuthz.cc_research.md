# sources/distributed-fs/eos/mgm/authz/XrdMgmAuthz.cc

Purpose: implements the XRootD authorization plugin entry points for EOS MGM and a minimal `XrdMgmAuthz::Access` decision. The plugin primarily ensures requests have an authenticated identity or EOS token before allowing XRootD-layer access; deeper authorization is handled by MGM logic.

Important APIs and functions: global `gMgmAuthz` stores the singleton plugin instance. `XrdAccAuthorizeObject` creates or returns it and emits version/initialization messages. `XrdAccAuthorizeObjAdd` rejects chaining and delegates to the main factory. `XrdMgmAuthz::Access` logs path/env/entity, grants all privileges for EOS token environments, requires either `Entity->name` or entity attribute `request.name`, and otherwise returns no privileges.

Control flow: plugin construction is lazy and singleton. Access decisions are intentionally coarse: EOS token means `XrdAccPriv_All`; missing entity/name means `XrdAccPriv_None`; otherwise all privileges are granted.

State and persistence: only the process-global plugin pointer is retained. No policy is persisted here.

Dependencies and integration points: depends on XRootD `XrdAccAuthorize`, `XrdSysError`, `XrdOucEnv`, `XrdSecEntityAttr`, version macros, EOS token detection, security entity logging, and EOS logging. It plugs into XRootD via the C symbols expected by `authlib`.

Risks: `Test` in the header always returns deny, so callers must use `Access` results directly or this implementation would fail privilege tests. The broad `XrdAccPriv_All` return means MGM request handlers must enforce actual authorization. Plugin chaining is explicitly unsupported. Entity attribute API use assumes `eaAPI` exists when `Entity` exists.

Test signals: plugin load tests should verify singleton behavior, duplicate load messages, no-chaining behavior, EOS token grant, null entity denial, request-name fallback, and compatibility with XRootD versions used in deployment.
