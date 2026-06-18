# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/security/http/RestCsrfPreventionFilter.java

## Purpose

`RestCsrfPreventionFilter` protects Hadoop REST endpoints by requiring browser-originated, state-changing requests to carry a configured anti-CSRF header.

## Important APIs, Types, and Functions

It exposes init params `browser-useragents-regex`, `custom-header`, and `methods-to-ignore`; defaults are browser regexes `^Mozilla.*`/`^Opera.*`, header `X-XSRF-HEADER`, and ignored methods `GET,OPTIONS,HEAD,TRACE`. Important methods are `init`, `parseBrowserUserAgents`, `parseMethodsToIgnore`, `isBrowser`, `handleHttpInteraction`, `doFilter`, and static `getFilterParams`. Nested `HttpInteraction` abstracts servlet and non-servlet integrations.

## Control Flow

Initialization compiles browser regex patterns and method ignore sets. `handleHttpInteraction` allows the request if the user agent is not considered a browser, the method is ignored, or the required header exists; otherwise it sends HTTP 400. The servlet adapter wraps `HttpServletRequest`, `HttpServletResponse`, and `FilterChain`.

## State and Persistence Behavior

State is per-filter instance: header name, ignored method set, and browser regex set. There is no persistence.

## Dependencies and Integration Points

It depends on Servlet APIs, Jetty `Response` for reason phrase handling, Hadoop `Configuration.getPropsWithPrefix`, and SLF4J. It integrates with Hadoop web UI/REST filter chains and can be used through the abstract `HttpInteraction`.

## Risks and Edge Cases

Method parsing does not trim values, so spaces in config can break matching. Browser detection depends entirely on regex config and ignores null user agents. Only header presence is checked, not value. Jetty-specific status reason behavior is conditional.

## Test Signals

Tests should cover browser/non-browser user agents, default ignored methods, custom header names, missing-header 400, custom method list whitespace behavior, `getFilterParams`, and servlet adapter response behavior.
