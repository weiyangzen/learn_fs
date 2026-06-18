# sources/distributed-fs/ceph-client/tools/perf/ui/gtk/helpline.c

## Purpose

`gtk/helpline.c` adapts perf's generic helpline interface to GTK statusbar output.

## Important APIs, Types, and Functions

It defines `gtk_helpline_pop`, `gtk_helpline_push`, `gtk_helpline_show`, a `struct ui_helpline gtk_helpline_fns`, and the public initializer `perf_gtk__init_helpline`.

## Control Flow and State

Push/pop no-op when `pgctx` is inactive; otherwise they use the GTK statusbar and stored context ID. `gtk_helpline_show` accumulates formatted text into `ui_helpline__current` until a newline is seen, then displays only the first line and resets the static backlog.

## Dependencies and Integration Points

It depends on `gtk.h`, generic `ui/helpline.h`, and `ui_helpline__current`. `perf_gtk__init` installs these operations so generic `ui__warning` and helpline calls show in GTK.

## Risks and Test Signals

Risks are backlog overflow/truncation and lost multiline messages. Tests should push, pop, and show warnings before and after GTK context activation, including multiline messages.
