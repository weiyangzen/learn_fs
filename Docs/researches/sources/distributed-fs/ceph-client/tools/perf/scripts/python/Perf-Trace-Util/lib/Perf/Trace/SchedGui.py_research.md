<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/SchedGui.py -->
# sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/SchedGui.py
Purpose: wxPython GUI frame for visualizing scheduler trace rectangles and summaries. It is support code for scheduler visualization scripts.

Important APIs/types/functions: `RootFrame` owns window dimensions, zoom, scroll settings, and the scheduler tracer adapter. Methods convert time to pixels, track scroll origin, paint rectangle zones, request visible data from `sched_tracer.fill_zone`, map mouse coordinates to rectangles, update summary text, zoom, and handle key/mouse events.

Control flow: Construction initializes wx frame/panels/scrollbars, binds paint/key/mouse events, asks the tracer for interval and rectangle count, and shows the frame. Paint events compute visible time range and call into the tracer. Mouse clicks identify a rectangle and timestamp and dispatch to `sched_tracer.mouse_down`. Keyboard events zoom or scroll.

State and persistence: Maintains GUI state such as `zoom`, virtual width/height, screen dimensions, current `wx.PaintDC`, and optional summary text widget. No persistent files.

Dependencies and integration points: Requires `wx`/wxPython and a `sched_tracer` object implementing `set_root_win`, `interval`, `nr_rectangles`, `fill_zone`, and `mouse_down`.

Risks: Uses older wx APIs such as `GetPositionTuple`, and Python 2-era division may produce floats where wx expects ints. Missing wxPython raises ImportError. Rendering depends on tracer callbacks being efficient.

Test signals: Manual GUI test with a scheduler tracer should show rectangles, respond to mouse selection, and zoom/scroll with keyboard controls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/scripts/python/Perf-Trace-Util/lib/Perf/Trace/SchedGui.py -->
