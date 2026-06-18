# sources/distributed-fs/orangefs/src/apps/karma/color.c

## Purpose
`color.c` provides a small GTK/GDK helper for Karma graph rendering. It creates a new foreground `GdkGC` configured to a requested RGB color in 0-255 component space.

## Important APIs, Types, and Functions
The single public function is `gui_get_new_fg_color_gc(GtkWidget *drawing_area, gint red, gint green, gint blue)`. It asserts component ranges, allocates a `GdkColor`, converts 8-bit channels to 16-bit GDK channels, creates a graphics context with `gdk_gc_new(drawing_area->window)`, allocates the color in the widget colormap, and applies it with `gdk_gc_set_foreground()`.

## Control Flow
There is no branching beyond assertions. Callers pass a realized drawing area and color components; the function returns a new GC to own/use for drawing.

## State and Persistence
The function allocates a `GdkColor` and a `GdkGC`. The GC is returned to the caller; the `GdkColor` allocation is not freed in this function. Runtime state is therefore GDK resource state attached to a widget/window, not persistent storage.

## Dependencies and Integration Points
It depends on GTK2/GDK and is used by `status.c` and `traffic.c` during drawing-area configure events to create red, green, blue, yellow, orange, and purple graphics contexts.

## Risks and Edge Cases
The helper assumes `drawing_area->window` is valid, so it must be called after widget realization/configuration. The allocated `GdkColor` is leaked. In long-running dashboards with repeated configure events, repeated calls can accumulate small heap leaks in addition to GDK resource churn. Assertions disappear in release builds if `NDEBUG` is used, leaving no runtime validation of component ranges.

## Test Signals
Resize the Karma status and traffic drawing areas repeatedly under leak detection. Verify returned GCs draw expected colors after configure events. Add a test or assertion harness for invalid component values and unrealized widgets if this helper is modernized.
