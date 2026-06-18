# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/dp/dp_debug.c

Purpose: Provides optional debugfs files for MSM DP runtime state and compliance test controls when `CONFIG_DEBUG_FS` is enabled.

Important APIs/functions: `msm_dp_debug_init()` allocates private debug state and creates `dp_debug`; for non-eDP it also creates `dp_test_active`, `dp_test_data`, and `dp_test_type`. `msm_dp_debug_show()` reports link capabilities, mode timings, bpp, sink request, lane count/rate, link clock, and PHY levels. `msm_dp_test_data_show()` reports requested compliance video dimensions and bpc. `msm_dp_test_type_show()` reports video pattern type. `msm_dp_test_active_write()` toggles `panel->video_test`, accepting only value `1` as active.

Control flow: Debugfs read callbacks dereference live panel/link/connector state and print through seq_file. The active write copies user input with `memdup_user_nul()`, parses decimal, and changes test state only when connector is connected. eDP skips compliance files.

State and persistence: Private debug object stores pointers to link, panel, and connector. `panel->video_test` is mutable runtime state; debugfs files do not persist.

Dependencies/integration: Depends on debugfs, DRM connector/file helpers, DP AUX/CTRL/display/link/panel structures, and DRM DP helper conversions.

Risks and test signals: Debug state stores raw pointers and assumes connector/panel/link lifetimes exceed debugfs files. The files are created with mode `0444`, but `dp_test_active` has a write handler, making write availability depend on debugfs permission behavior. Test debugfs reads while connected/disconnected, compliance toggling, eDP path, connector removal, and builds with debugfs disabled.
