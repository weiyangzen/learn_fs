# sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/util/ServletUtil.java

## Purpose
`ServletUtil` contains small servlet/JSP helpers for Hadoop web UIs: basic HTML framing, request parameter normalization/parsing, footer generation, and raw servlet path extraction.

## Important APIs, Types, And Functions
Important APIs are `initHTML`, `getParameter`, `parseLongParam`, `htmlFooter`, `getRawPath`, and constant `HTML_TAIL`.

## Control Flow
`initHTML` sets `text/html`, obtains a writer, and writes a simple page header and stylesheet link. `getParameter` trims whitespace and maps empty strings to null. `parseLongParam` requires a parameter and parses it with `Long.parseLong`. `getRawPath` checks that `requestURI` starts with `servletName + "/"` and returns the substring after the servlet name without URL decoding.

## State And Persistence
There is no mutable state. `HTML_TAIL` includes the year captured at class initialization.

## Dependencies And Integration Points
It depends on Java servlet APIs, `HttpServletRequest`, `Calendar`, Hadoop annotations, and `Preconditions`. It is used by Hadoop web UI servlets and JSPs.

## Risks
`initHTML` writes unescaped titles directly into HTML, so callers must provide safe text. `parseLongParam` lets `NumberFormatException` propagate despite declaring `IOException`. `HTML_TAIL` year can become stale in long-running daemons across New Year.

## Test Signals
Tests should cover content type/header output, parameter trimming, missing and invalid long parsing, raw path extraction, precondition failures, and HTML escaping expectations at callers.
