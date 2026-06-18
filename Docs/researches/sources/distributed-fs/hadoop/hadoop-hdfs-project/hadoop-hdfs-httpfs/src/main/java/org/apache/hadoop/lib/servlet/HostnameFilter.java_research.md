# sources/distributed-fs/hadoop/hadoop-hdfs-project/hadoop-hdfs-httpfs/src/main/java/org/apache/hadoop/lib/servlet/HostnameFilter.java

## Purpose
`HostnameFilter` resolves the remote client address for the current servlet request and exposes the canonical hostname to later code through a request-thread `ThreadLocal`.

## Important APIs, Types, and Functions
The class implements `Filter`, uses `InetAddress.getByName(request.getRemoteAddr()).getCanonicalHostName()`, and exposes `public static String get()` to retrieve the hostname. Unknown or null addresses become the sentinel string `"???"` and are logged with SLF4J.

## Control Flow
`doFilter` resolves the hostname before invoking the downstream chain, stores it in `HOSTNAME_TL`, delegates to `chain.doFilter`, and always removes the ThreadLocal in `finally`.

## State and Persistence
Only per-thread transient state is stored. No filesystem or configuration persistence occurs.

## Dependencies and Integration Points
`MDCFilter` can read `HostnameFilter.get()` to add `hostname` to logging MDC. The HttpFS `web.xml` files register both filters. In the descriptors read here, `MDCFilter` is mapped before `hostnameFilter`, so the hostname value will only be visible to MDC if container ordering or another mapping causes hostname to run first; otherwise MDC will omit the hostname.

## Risks
Reverse DNS lookup can block request handling or produce environment-dependent names. The SLF4J warning for `UnknownHostException` uses a `{0}` token rather than the usual `{}`, which may reduce message clarity. The ThreadLocal model has the same async-thread limitation as other servlet filters in this package.

## Test Signals
Direct tests outside this subset (`TestHostnameFilter`) assert resolution for localhost, fallback to `"???"`, and cleanup after request completion. In this subset, `MDCFilter` and web descriptors are the primary integration signals.
