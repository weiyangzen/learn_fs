# `sources/distributed-fs/hadoop/hadoop-common-project/hadoop-common/src/main/java/org/apache/hadoop/conf/ReconfigurationServlet.java`

## Purpose

`ReconfigurationServlet` is an HTML servlet for viewing proposed configuration changes and applying approved runtime reconfiguration to a registered `Reconfigurable` component.

## Important APIs and Types

The servlet exposes `CONF_SERVLET_RECONFIGURABLE_PREFIX`, overrides `doGet` and `doPost`, and uses private helpers `getReconfigurable`, `printHeader`, `printFooter`, `printConf`, `getParams`, and `applyChanges`. It extends `HttpServlet`.

## Control Flow

The servlet looks up the target `Reconfigurable` from the servlet context using the prefix plus request servlet path. `doGet` creates a fresh `Configuration`, compares it with the current component configuration via `ReconfigurationUtil.getChangedProperties`, renders each change, marks non-reconfigurable properties in red, and includes hidden form fields for allowed changes. `doPost` creates a new fresh configuration again, then iterates submitted parameters under synchronization on the old configuration. It only applies a submitted value if it still matches the freshly loaded value or represents default/null/empty reset, then calls `reconfigureProperty`; otherwise it reports that the value changed since approval.

## State and Persistence

The servlet stores no per-request state beyond inherited servlet state. Runtime changes are delegated to the target `Reconfigurable`; it does not persist changes to configuration files.

## Dependencies and Integration Points

It depends on Java Servlet APIs, Apache Commons Text HTML escaping/unescaping, `ReconfigurationUtil`, `Configuration`, `Reconfigurable`, `ReconfigurationException`, and `StringUtils.stringifyException`. It is integrated by daemon web apps that publish a `Reconfigurable` context attribute.

## Risks

Authentication and authorization are not handled in this class, so deployment must protect the servlet. Hidden form fields trust client-submitted names and values but revalidate against a freshly loaded configuration before applying. Values are HTML-escaped for rendering, but exception responses may include raw exception messages from lower layers. A missing context attribute causes null dereference. The page uses simple HTML and does not redact property values, so it can expose sensitive configuration unless upstream access controls and property choice prevent it.

## Test Signals

Tests should cover context lookup, GET rendering for allowed/disallowed changes, HTML escaping of names/values, POST reset semantics, stale-value rejection, exception-to-500 behavior, synchronization with the old configuration, and access-control behavior in the hosting web app.
